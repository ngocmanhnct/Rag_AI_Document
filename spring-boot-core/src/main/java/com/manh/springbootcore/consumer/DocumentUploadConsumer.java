package com.manh.springbootcore.consumer;

import com.manh.springbootcore.config.RabbitMQConfig;
import com.manh.springbootcore.dto.message.DocumentUploadMessage;
import com.manh.springbootcore.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class DocumentUploadConsumer {

    private final DocumentService documentService;

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void handleUpload(DocumentUploadMessage message) {
        documentService.processUpload(message);
    }
}