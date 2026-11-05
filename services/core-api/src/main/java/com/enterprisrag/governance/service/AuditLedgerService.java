package com.enterprisrag.governance.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AuditLedgerService {

    private static final Logger log = LoggerFactory.getLogger(AuditLedgerService.class);

    @Autowired(required = false)
    private JdbcTemplate jdbcTemplate;

    @Async
    public void recordAuditEntry(
            String traceId,
            String tenantId,
            String userId,
            String eventType,
            int rawLength,
            int sanitizedLength,
            List<String> piiTypes,
            String guardrailStatus,
            long executionTimeMs) {

        log.info("audit_transaction_ledger: traceId={}, tenantId={}, status={}, duration={}ms",
                traceId, tenantId, guardrailStatus, executionTimeMs);

        if (jdbcTemplate == null) {
            return;
        }

        try {
            String sql = """
                INSERT INTO audit_logs (
                    trace_id, tenant_id, user_id, event_type, prompt_raw_length,
                    prompt_sanitized_length, pii_entities_detected, guardrail_status,
                    execution_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?::text[], ?, ?);
            """;

            String[] piiArray = piiTypes != null ? piiTypes.toArray(new String[0]) : new String[0];
            String piiPgArray = "{" + String.join(",", piiArray) + "}";

            jdbcTemplate.update(
                    sql,
                    traceId,
                    tenantId != null ? tenantId : "default-tenant",
                    userId != null ? userId : "anonymous-user",
                    eventType,
                    rawLength,
                    sanitizedLength,
                    piiPgArray,
                    guardrailStatus,
                    (int) executionTimeMs
            );
        } catch (Exception e) {
            log.warn("audit_log_database_write_deferred: {}", e.getMessage());
        }
    }

    public List<java.util.Map<String, Object>> getRecentAuditLogs(int limit) {
        if (jdbcTemplate == null) {
            return List.of();
        }
        try {
            String sql = """
                SELECT id::text AS id, trace_id, event_type, guardrail_status, 
                       array_to_json(pii_entities_detected)::text AS pii_json, 
                       execution_time_ms, created_at::text AS created_at
                FROM audit_logs
                ORDER BY created_at DESC
                LIMIT ?;
            """;
            return jdbcTemplate.query(sql, (rs, rowNum) -> {
                java.util.Map<String, Object> map = new java.util.HashMap<>();
                map.put("id", rs.getString("id"));
                map.put("trace_id", rs.getString("trace_id"));
                map.put("event_type", rs.getString("event_type"));
                map.put("guardrail_status", rs.getString("guardrail_status"));
                map.put("pii_entities_detected", rs.getString("pii_json"));
                map.put("execution_time_ms", rs.getInt("execution_time_ms"));
                map.put("created_at", rs.getString("created_at"));
                return map;
            }, limit);
        } catch (Exception e) {
            log.error("audit_log_fetch_error: {}", e.getMessage());
            return List.of();
        }
    }
}

