package com.enterprisrag.governance.guardrails;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class PiiSanitizerTest {

    private PiiVaultService piiVaultService;

    @BeforeEach
    void setUp() {
        piiVaultService = new PiiVaultService();
    }

    @Test
    @DisplayName("Should detect and tokenize SSN reversibly")
    void shouldTokenizeSsnReversibly() {
        String prompt = "Please check reimbursement for employee with SSN 123-45-6789 and name John.";
        String traceId = "test-trace-1";

        GuardrailOutcome outcome = piiVaultService.tokenizePii(prompt, traceId);

        assertEquals("SANITIZED", outcome.getStatus());
        assertTrue(outcome.getDetectedPiiTypes().contains("SSN"));
        assertFalse(outcome.getSanitizedPrompt().contains("123-45-6789"));
        assertTrue(outcome.getSanitizedPrompt().contains("[TOKEN_SSN_"));

        // Test egress de-anonymization
        String restored = piiVaultService.restorePii(outcome.getSanitizedPrompt(), traceId);
        assertEquals(prompt, restored);
    }

    @Test
    @DisplayName("Should detect email addresses and tokenize")
    void shouldTokenizeEmail() {
        String prompt = "Send invoice to finance.dept@enterprise.corp immediately.";
        String traceId = "test-trace-2";

        GuardrailOutcome outcome = piiVaultService.tokenizePii(prompt, traceId);

        assertEquals("SANITIZED", outcome.getStatus());
        assertTrue(outcome.getDetectedPiiTypes().contains("EMAIL"));
        assertFalse(outcome.getSanitizedPrompt().contains("finance.dept@enterprise.corp"));

        String restored = piiVaultService.restorePii(outcome.getSanitizedPrompt(), traceId);
        assertEquals(prompt, restored);
    }

    @Test
    @DisplayName("Should keep clean prompt untouched")
    void shouldKeepCleanPromptUntouched() {
        String prompt = "What are the core benefits of our enterprise cloud solution?";
        String traceId = "test-trace-3";

        GuardrailOutcome outcome = piiVaultService.tokenizePii(prompt, traceId);

        assertEquals("CLEAN", outcome.getStatus());
        assertTrue(outcome.getDetectedPiiTypes().isEmpty());
        assertEquals(prompt, outcome.getSanitizedPrompt());
    }
}

