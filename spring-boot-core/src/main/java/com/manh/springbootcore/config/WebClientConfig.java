package com.manh.springbootcore.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Value("${rag.service.url}")
    private String ragServiceUrl;

    @Bean
    public WebClient ragServiceWebClient() {
        return WebClient.builder()
                .baseUrl(ragServiceUrl)
                .build();
    }
}