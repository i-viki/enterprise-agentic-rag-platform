package com.enterprisrag.governance.config;

import org.springframework.context.annotation.Configuration;

import java.util.UUID;

@Configuration
public class OpenTelemetryConfig {

    public static String generateTraceId() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    public static String createTraceparent(String traceId) {
        String spanId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        return String.format("00-%s-%s-01", traceId, spanId);
    }
}

