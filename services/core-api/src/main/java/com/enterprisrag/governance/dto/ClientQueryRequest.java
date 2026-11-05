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
public class ClientQueryRequest {
    private String prompt;
    private String threadId;
    private String userId;
    private String tenantId;
    private Integer clearanceLevel;
    private List<String> userRoles;
}

