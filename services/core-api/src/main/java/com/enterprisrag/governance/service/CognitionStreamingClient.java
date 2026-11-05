package com.enterprisrag.governance.service;

import com.enterprisrag.governance.config.OpenTelemetryConfig;
import com.enterprisrag.governance.dto.SanitizedServicePayload;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;

@Service
public class CognitionStreamingClient {

    private static final Logger log = LoggerFactory.getLogger(CognitionStreamingClient.class);

    private final WebClient webClient;

    public CognitionStreamingClient(
            WebClient.Builder webClientBuilder,
            @Value("${ai.engine.base-url:http://localhost:8000}") String engineBaseUrl) {
        this.webClient = webClientBuilder.baseUrl(engineBaseUrl).build();
    }

    /**
     * Executes non-streaming cognitive cycle against Python FastAPI engine.
     */
    public Mono<Map> forwardToEngine(SanitizedServicePayload payload) {
        String traceparent = OpenTelemetryConfig.createTraceparent(payload.getTraceId());

        return webClient.post()
                .uri("/v1/agent/cognition")
                .header("traceparent", traceparent)
                .header("X-Trace-Id", payload.getTraceId())
                .header("X-Tenant-Id", payload.getTenantId())
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(Duration.ofSeconds(90))
                .doOnError(e -> log.error("failed_to_reach_python_engine: traceId={}, error={}", payload.getTraceId(), e.getMessage()));
    }

    /**
     * Streams tokens from Python FastAPI engine via Server-Sent Events (SSE).
     */
    public Flux<String> streamFromEngine(SanitizedServicePayload payload) {
        String traceparent = OpenTelemetryConfig.createTraceparent(payload.getTraceId());

        return webClient.post()
                .uri("/v1/agent/cognition/stream")
                .header("traceparent", traceparent)
                .header("X-Trace-Id", payload.getTraceId())
                .header("X-Tenant-Id", payload.getTenantId())
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class)
                .timeout(Duration.ofSeconds(60))
                .onErrorResume(e -> {
                    log.error("streaming_error_from_python_engine: traceId={}, error={}", payload.getTraceId(), e.getMessage());
                    return Flux.just("event: error\ndata: {\"error\": \"Engine connection failed\"}\n\n");
                });
    }
}

