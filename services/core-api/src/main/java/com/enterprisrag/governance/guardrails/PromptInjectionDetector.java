package com.enterprisrag.governance.guardrails;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.regex.Pattern;

@Service
public class PromptInjectionDetector {

    private static final Logger log = LoggerFactory.getLogger(PromptInjectionDetector.class);

    private static final List<Pattern> INJECTION_PATTERNS = List.of(
            Pattern.compile("(?i)ignore\\s+(all\\s+)?(previous|prior)\\s+instructions"),
            Pattern.compile("(?i)disregard\\s+(all\\s+)?(previous|prior)\\s+rules"),
            Pattern.compile("(?i)you\\s+are\\s+now\\s+(an?\\s+)?unrestricted"),
            Pattern.compile("(?i)developer\\s+mode\\s+(enabled|on)"),
            Pattern.compile("(?i)system\\s+prompt\\s+override"),
            Pattern.compile("(?i)<\\|im_start\\|>"),
            Pattern.compile("(?i)<\\|im_end\\|>"),
            Pattern.compile("(?i)###\\s*System:"),
            Pattern.compile("(?i)bypass\\s+(guardrail|safety|filter)"),
            Pattern.compile("(?i)reveal\\s+(all\\s+)?(secret|internal|system)\\s+(keys?|instructions?|tokens?)")
    );

    public boolean isMalicious(String prompt) {
        if (prompt == null || prompt.isBlank()) {
            return false;
        }

        for (Pattern pattern : INJECTION_PATTERNS) {
            if (pattern.matcher(prompt).find()) {
                log.warn("prompt_injection_heuristic_triggered: pattern='{}'", pattern.pattern());
                return true;
            }
        }

        return false;
    }
}

