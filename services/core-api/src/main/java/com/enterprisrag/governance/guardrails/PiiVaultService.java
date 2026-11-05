package com.enterprisrag.governance.guardrails;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class PiiVaultService {

    private static final Logger log = LoggerFactory.getLogger(PiiVaultService.class);
    private static final Duration PII_TOKEN_TTL = Duration.ofMinutes(15);

    // Fallback in-memory map when Redis is offline or disabled
    private final Map<String, String> localVaultFallback = new ConcurrentHashMap<>();

    @Autowired(required = false)
    private StringRedisTemplate redisTemplate;

    // Standard Enterprise PII Patterns
    private static final Pattern SSN_PATTERN = Pattern.compile("\\b(?!000|666|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0000)\\d{4}\\b");
    private static final Pattern EMAIL_PATTERN = Pattern.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}");
    private static final Pattern CREDIT_CARD_PATTERN = Pattern.compile("\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\\b");
    private static final Pattern PHONE_PATTERN = Pattern.compile("\\b(?:\\+?1[-.\\s]?)?\\(?([0-9]{3})\\)?[-.\\s]?([0-9]{3})[-.\\s]?([0-9]{4})\\b");

    /**
     * Reversibly tokenizes detected PII entities in the input prompt.
     */
    public GuardrailOutcome tokenizePii(String rawPrompt, String traceId) {
        if (rawPrompt == null || rawPrompt.isBlank()) {
            return GuardrailOutcome.builder()
                    .status("CLEAN")
                    .sanitizedPrompt(rawPrompt)
                    .build();
        }

        String sanitized = rawPrompt;
        List<String> detectedTypes = new ArrayList<>();
        Map<String, String> sessionTokenMap = new HashMap<>();

        // 1. SSN Redaction
        sanitized = redactPattern(sanitized, SSN_PATTERN, "SSN", traceId, detectedTypes, sessionTokenMap);

        // 2. Credit Card Redaction
        sanitized = redactPattern(sanitized, CREDIT_CARD_PATTERN, "CREDIT_CARD", traceId, detectedTypes, sessionTokenMap);

        // 3. Email Redaction
        sanitized = redactPattern(sanitized, EMAIL_PATTERN, "EMAIL", traceId, detectedTypes, sessionTokenMap);

        // 4. Phone Redaction
        sanitized = redactPattern(sanitized, PHONE_PATTERN, "PHONE", traceId, detectedTypes, sessionTokenMap);

        // Store mappings in Redis or Local Vault
        sessionTokenMap.forEach(this::storeToken);

        String status = detectedTypes.isEmpty() ? "CLEAN" : "SANITIZED";

        return GuardrailOutcome.builder()
                .status(status)
                .sanitizedPrompt(sanitized)
                .detectedPiiTypes(detectedTypes)
                .notes(detectedTypes.isEmpty() ? List.of() : List.of("PII entities pseudonymized into reversible vault tokens"))
                .build();
    }

    /**
     * Restores pseudonymized tokens back into real values exclusively for authorized client response egress.
     */
    public String restorePii(String text, String traceId) {
        if (text == null || text.isBlank() || !text.contains("[TOKEN_")) {
            return text;
        }

        String restored = text;
        Pattern tokenPattern = Pattern.compile("\\[TOKEN_[A-Z_]+_[a-f0-9]{8}\\]");
        Matcher matcher = tokenPattern.matcher(text);

        while (matcher.find()) {
            String token = matcher.group();
            String rawValue = retrieveToken(token);
            if (rawValue != null) {
                restored = restored.replace(token, rawValue);
            }
        }

        return restored;
    }

    private String redactPattern(String text, Pattern pattern, String entityType, String traceId,
                                 List<String> detectedTypes, Map<String, String> tokenMap) {
        Matcher matcher = pattern.matcher(text);
        StringBuilder sb = new StringBuilder();

        while (matcher.find()) {
            String rawMatch = matcher.group();
            if (!detectedTypes.contains(entityType)) {
                detectedTypes.add(entityType);
            }
            String tokenHash = UUID.randomUUID().toString().substring(0, 8);
            String tokenKey = String.format("[TOKEN_%s_%s]", entityType, tokenHash);

            tokenMap.put(tokenKey, rawMatch);
            matcher.appendReplacement(sb, Matcher.quoteReplacement(tokenKey));
        }
        matcher.appendTail(sb);
        return sb.toString();
    }

    private void storeToken(String tokenKey, String rawValue) {
        try {
            if (redisTemplate != null) {
                redisTemplate.opsForValue().set("pii:" + tokenKey, rawValue, PII_TOKEN_TTL);
            } else {
                localVaultFallback.put(tokenKey, rawValue);
            }
        } catch (Exception e) {
            log.warn("redis_pii_vault_write_failed_using_local_fallback: {}", e.getMessage());
            localVaultFallback.put(tokenKey, rawValue);
        }
    }

    private String retrieveToken(String tokenKey) {
        try {
            if (redisTemplate != null) {
                String val = redisTemplate.opsForValue().get("pii:" + tokenKey);
                if (val != null) {
                    return val;
                }
            }
        } catch (Exception e) {
            log.warn("redis_pii_vault_read_failed: {}", e.getMessage());
        }
        return localVaultFallback.get(tokenKey);
    }
}

