package com.enterprisrag.governance.config;

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Configuration
public class ResilienceConfig {

    private final Map<String, Bucket> bucketCache = new ConcurrentHashMap<>();

    /**
     * Resolves token bucket for rate-limiting. Standard enterprise tier: 20 queries / minute.
     */
    public Bucket resolveBucket(String key) {
        return bucketCache.computeIfAbsent(key, k -> Bucket.builder()
                .addLimit(Bandwidth.builder()
                        .capacity(20)
                        .refillGreedy(20, Duration.ofMinutes(1))
                        .build())
                .build());
    }
}

