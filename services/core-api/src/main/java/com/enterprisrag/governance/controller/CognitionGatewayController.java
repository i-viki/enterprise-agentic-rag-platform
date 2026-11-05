package com.enterprisrag.governance.controller;

import com.enterprisrag.governance.config.OpenTelemetryConfig;
import com.enterprisrag.governance.config.ResilienceConfig;
import com.enterprisrag.governance.dto.ClientQueryRequest;
import com.enterprisrag.governance.dto.ClientQueryResponse;
import com.enterprisrag.governance.dto.SanitizedServicePayload;
import com.enterprisrag.governance.guardrails.GuardrailOutcome;
import com.enterprisrag.governance.guardrails.LocalModelGuardClient;
import com.enterprisrag.governance.guardrails.PiiVaultService;
import com.enterprisrag.governance.guardrails.PromptInjectionDetector;
import com.enterprisrag.governance.service.AuditLedgerService;
import com.enterprisrag.governance.service.CognitionStreamingClient;
import io.github.bucket4j.Bucket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/cognition")
public class CognitionGatewayController {

    private static final Logger log = LoggerFactory.getLogger(CognitionGatewayController.class);

    private final PiiVaultService piiVaultService;
    private final PromptInjectionDetector injectionDetector;
    private final LocalModelGuardClient guardClient;
    private final CognitionStreamingClient engineClient;
    private final AuditLedgerService auditLedgerService;
    private final ResilienceConfig resilienceConfig;

    public CognitionGatewayController(
            PiiVaultService piiVaultService,
            PromptInjectionDetector injectionDetector,
            LocalModelGuardClient guardClient,
            CognitionStreamingClient engineClient,
            AuditLedgerService auditLedgerService,
            ResilienceConfig resilienceConfig) {
        this.piiVaultService = piiVaultService;
        this.injectionDetector = injectionDetector;
        this.guardClient = guardClient;
        this.engineClient = engineClient;
        this.auditLedgerService = auditLedgerService;
        this.resilienceConfig = resilienceConfig;
    }

    @PostMapping("/query")
    public Mono<ResponseEntity<Object>> submitQuery(@RequestBody ClientQueryRequest request) {
        long startTime = System.currentTimeMillis();
        String traceId = OpenTelemetryConfig.generateTraceId();
        String clientKey = request.getUserId() != null ? request.getUserId() : "anonymous-client";

        // 1. Rate Limiting Check (Token Bucket)
        Bucket bucket = resilienceConfig.resolveBucket(clientKey);
        if (!bucket.tryConsume(1)) {
            auditLedgerService.recordAuditEntry(traceId, request.getTenantId(), request.getUserId(),
                    "QUERY_ATTEMPT", request.getPrompt().length(), 0, List.of(), "BLOCKED",
                    System.currentTimeMillis() - startTime);
            return Mono.just(ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                    .body(Map.of("error", "Rate limit exceeded. Please throttle your requests.")));
        }

        // 2. Prompt Injection Heuristics (Tier-1)
        if (injectionDetector.isMalicious(request.getPrompt())) {
            auditLedgerService.recordAuditEntry(traceId, request.getTenantId(), request.getUserId(),
                    "PROMPT_INJECTION_BLOCKED", request.getPrompt().length(), 0, List.of(), "BLOCKED",
                    System.currentTimeMillis() - startTime);
            return Mono.just(ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "Safety Policy Violation: Malicious prompt pattern detected.")));
        }

        // 3. PII Tokenization (Tier-1 Reversible Vault)
        GuardrailOutcome piiOutcome = piiVaultService.tokenizePii(request.getPrompt(), traceId);

        // 4. Local Model Guardrail Check (Tier-1.5 llama-guard3:1b)
        return guardClient.evaluateSafety(piiOutcome.getSanitizedPrompt())
                .flatMap(isSafe -> {
                    if (!isSafe) {
                        auditLedgerService.recordAuditEntry(traceId, request.getTenantId(), request.getUserId(),
                                "CONTENT_POLICY_BLOCKED", request.getPrompt().length(), 0, piiOutcome.getDetectedPiiTypes(), "BLOCKED",
                                System.currentTimeMillis() - startTime);
                        return Mono.just(ResponseEntity.status(HttpStatus.FORBIDDEN)
                                .body((Object) Map.of("error", "AI Safety Policy: Prompt classified as unsafe by model guardrail.")));
                    }

                    // 5. Forward Sanitized Query to Python LangGraph Engine
                    SanitizedServicePayload payload = SanitizedServicePayload.builder()
                            .traceId(traceId)
                            .threadId(request.getThreadId() != null ? request.getThreadId() : "default-thread")
                            .tenantId(request.getTenantId() != null ? request.getTenantId() : "tenant-enterprise-prod")
                            .userId(request.getUserId() != null ? request.getUserId() : "default_user")
                            .clearanceLevel(request.getClearanceLevel() != null ? request.getClearanceLevel() : 1)
                            .userRoles(request.getUserRoles() != null ? request.getUserRoles() : List.of("ALL"))
                            .sanitizedPrompt(piiOutcome.getSanitizedPrompt())
                            .build();

                    return engineClient.forwardToEngine(payload)
                            .map(engineResponse -> {
                                String rawAnswer = (String) engineResponse.get("generated_answer");
                                // 6. Egress De-anonymization (Restore PII for authorized client)
                                String restoredAnswer = piiVaultService.restorePii(rawAnswer, traceId);

                                long duration = System.currentTimeMillis() - startTime;
                                auditLedgerService.recordAuditEntry(traceId, request.getTenantId(), request.getUserId(),
                                        "COGNITION_QUERY_SUCCESS", request.getPrompt().length(),
                                        piiOutcome.getSanitizedPrompt().length(), piiOutcome.getDetectedPiiTypes(),
                                        piiOutcome.getStatus(), duration);

                                ClientQueryResponse response = ClientQueryResponse.builder()
                                        .traceId(traceId)
                                        .threadId(payload.getThreadId())
                                        .answer(restoredAnswer)
                                        .citations((List<Map<String, Object>>) engineResponse.get("citations"))
                                        .groundingScore((Double) engineResponse.get("grounding_score"))
                                        .isGrounded((Boolean) engineResponse.get("is_grounded"))
                                        .latencyMs(duration)
                                        .guardrailStatus(piiOutcome.getStatus())
                                        .build();

                                return ResponseEntity.ok((Object) response);
                            })
                            .onErrorResume(e -> {
                                long duration = System.currentTimeMillis() - startTime;
                                log.error("cognition_forwarding_error: traceId={}, error={}", traceId, e.getMessage());
                                return Mono.just(ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                                        .body(Map.of("error", "Cognition Engine currently unavailable", "trace_id", traceId)));
                            });
                });
    }

    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamQuery(@RequestBody ClientQueryRequest request) {
        String traceId = OpenTelemetryConfig.generateTraceId();

        // 1. Prompt Injection Heuristics
        if (injectionDetector.isMalicious(request.getPrompt())) {
            return Flux.just("event: error\ndata: {\"error\": \"Prompt injection detected\"}\n\n");
        }

        // 2. PII Redaction
        GuardrailOutcome piiOutcome = piiVaultService.tokenizePii(request.getPrompt(), traceId);

        SanitizedServicePayload payload = SanitizedServicePayload.builder()
                .traceId(traceId)
                .threadId(request.getThreadId() != null ? request.getThreadId() : "default-thread")
                .tenantId(request.getTenantId() != null ? request.getTenantId() : "tenant-enterprise-prod")
                .userId(request.getUserId() != null ? request.getUserId() : "default_user")
                .clearanceLevel(request.getClearanceLevel() != null ? request.getClearanceLevel() : 1)
                .userRoles(request.getUserRoles() != null ? request.getUserRoles() : List.of("ALL"))
                .sanitizedPrompt(piiOutcome.getSanitizedPrompt())
                .build();

        return engineClient.streamFromEngine(payload);
    }

    @GetMapping("/audit-logs")
    public Mono<ResponseEntity<List<Map<String, Object>>>> getAuditLogs(
            @RequestParam(defaultValue = "15") int limit) {
        return Mono.fromCallable(() -> auditLedgerService.getRecentAuditLogs(limit))
                .map(ResponseEntity::ok);
    }
}

