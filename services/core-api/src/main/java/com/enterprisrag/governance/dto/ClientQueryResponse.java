package com.enterprisrag.governance.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ClientQueryResponse {
    private String traceId;
    private String threadId;
    private String answer;
    private List<Map<String, Object>> citations;
    private Double groundingScore;
    private Boolean isGrounded;
    private Long latencyMs;
    private String guardrailStatus;
}

