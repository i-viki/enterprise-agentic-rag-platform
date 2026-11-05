package com.enterprisrag.governance.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StreamedTokenChunk {
    private String traceId;
    private String token;
    private Boolean isDone;
}

