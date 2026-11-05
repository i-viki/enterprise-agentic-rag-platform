package com.enterprisrag.governance.guardrails;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.List;
import java.util.Map;

@Service
public class LocalModelGuardClient {

    private static final Logger log = LoggerFactory.getLogger(LocalModelGuardClient.class);

    private final WebClient webClient;
    private final String guardModel;

    public LocalModelGuardClient(
            WebClient.Builder webClientBuilder,
            @Value("${ai.ollama.base-url:http://localhost:11434}") String ollamaBaseUrl,
            @Value("${ai.ollama.guard-model:llama-guard3:1b}") String guardModel) {
        this.webClient = webClientBuilder.baseUrl(ollamaBaseUrl).build();
        this.guardModel = guardModel;
    }

    /**
     * Calls local llama-guard3:1b over Ollama to evaluate prompt safety.
     * Returns true if safe, false if unsafe.
     */
    public Mono<Boolean> evaluateSafety(String prompt) {
        Map<String, Object> requestBody = Map.of(
                "model", guardModel,
                "messages", List.of(Map.of("role", "user", "content", prompt)),
                "stream", false
        );

        return webClient.post()
                .uri("/v1/chat/completions")
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(Duration.ofSeconds(2))
                .map(response -> {
                    List choices = (List) response.get("choices");
                    if (choices != null && !choices.isEmpty()) {
                        Map firstChoice = (Map) choices.get(0);
                        Map message = (Map) firstChoice.get("message");
                        String content = (String) message.get("content");
                        if (content != null && content.toLowerCase().contains("unsafe")) {
                            log.warn("llama_guard_classified_unsafe: model={}", guardModel);
                            return false;
                        }
                    }
                    return true;
                })
                .onErrorResume(e -> {
                    // Graceful fallback to true (relying on Tier-1 regex/heuristics) if local guard model is not yet booted
                    log.debug("llama_guard_fallback_mode_active: {}", e.getMessage());
                    return Mono.just(true);
                });
    }
}

