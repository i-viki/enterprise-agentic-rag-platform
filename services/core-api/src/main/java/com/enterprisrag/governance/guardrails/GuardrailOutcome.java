package com.enterprisrag.governance.guardrails;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GuardrailOutcome {
    private String status; // CLEAN, SANITIZED, BLOCKED
    private String sanitizedPrompt;
    @Builder.Default
    private List<String> detectedPiiTypes = new ArrayList<>();
    @Builder.Default
    private List<String> notes = new ArrayList<>();

    public boolean isBlocked() {
        return "BLOCKED".equalsIgnoreCase(this.status);
    }
}

