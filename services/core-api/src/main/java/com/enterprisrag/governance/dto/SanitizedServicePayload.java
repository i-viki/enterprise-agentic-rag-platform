package com.enterprisrag.governance.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SanitizedServicePayload {
    private String traceId;
    private String threadId;
    private String tenantId;
    private String userId;
    private Integer clearanceLevel;
    private List<String> userRoles;
    private String sanitizedPrompt;
    private String traceparent;
}

