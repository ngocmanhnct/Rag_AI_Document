package com.manh.springbootcore.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String QUEUE_NAME = "document.upload.queue";
    public static final String EXCHANGE_NAME = "document.exchange";
    public static final String ROUTING_KEY = "document.upload";

    @Bean
    public Queue documentUploadQueue() {
        return new Queue(QUEUE_NAME, true); // true = durable, sống sót qua restart RabbitMQ
    }

    @Bean
    public TopicExchange documentExchange() {
        return new TopicExchange(EXCHANGE_NAME);
    }

    @Bean
    public Binding binding(Queue documentUploadQueue, TopicExchange documentExchange) {
        return BindingBuilder.bind(documentUploadQueue).to(documentExchange).with(ROUTING_KEY);
    }

    @Bean
    public MessageConverter messageConverter() {
        // Jackson2JsonMessageConverter tự tạo ObjectMapper riêng, không đụng gì đến
        // câu chuyện Jackson 3 (tools.jackson) đã gặp ở phần trước - an toàn, không xung đột
        return new Jackson2JsonMessageConverter();
    }
}