package com.enterprisrag.governance.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/health")
public class HealthController {

    @GetMapping
    public Mono<Map<String, Object>> health() {
        return Mono.just(Map.of(
                "status", "UP",
                "service", "guardrail-governance-service",
                "tier", "Control Plane (Java 21)",
                "guardrails", Map.of(
                        "tier1_pii_vault", "ACTIVE",
                        "tier1_injection_detector", "ACTIVE",
                        "tier1_5_model_guard", "ACTIVE"
                )
        ));
    }
}

