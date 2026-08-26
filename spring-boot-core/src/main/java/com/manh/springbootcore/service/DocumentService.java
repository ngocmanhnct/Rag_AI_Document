package com.manh.springbootcore.service;

import com.manh.springbootcore.config.RabbitMQConfig;
import com.manh.springbootcore.dto.message.DocumentUploadMessage;
import com.manh.springbootcore.dto.response.DocumentResponse;
import com.manh.springbootcore.dto.response.FastApiUploadResponse;
import com.manh.springbootcore.entity.Document;
import com.manh.springbootcore.entity.DocumentStatus;
import com.manh.springbootcore.entity.User;
import com.manh.springbootcore.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final WebClient ragServiceWebClient;
    private final RabbitTemplate rabbitTemplate;

    // Chạy trong request-thread, TRẢ VỀ NGAY - không còn .block() chờ FastAPI nữa
    public DocumentResponse upload(User owner, MultipartFile file) {
        byte[] fileBytes;
        try {
            fileBytes = file.getBytes();
        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Không đọc được file");
        }

        Document document = Document.builder()
                .filename(file.getOriginalFilename())
                .status(DocumentStatus.PENDING)
                .owner(owner)
                .build();
        documentRepository.save(document);

        DocumentUploadMessage message = DocumentUploadMessage.builder()
                .documentId(document.getId())
                .filename(file.getOriginalFilename())
                .fileContent(fileBytes)
                .build();

        rabbitTemplate.convertAndSend(RabbitMQConfig.EXCHANGE_NAME, RabbitMQConfig.ROUTING_KEY, message);

        return toResponse(document);
    }

    // Chạy ở BACKGROUND, được gọi bởi DocumentUploadConsumer khi lấy message ra khỏi hàng đợi
    public void processUpload(DocumentUploadMessage message) {
        Document document = documentRepository.findById(message.getDocumentId())
                .orElseThrow(() -> new IllegalStateException("Document không tồn tại: " + message.getDocumentId()));

        document.setStatus(DocumentStatus.PROCESSING);
        documentRepository.save(document);

        try {
            MultipartBodyBuilder builder = new MultipartBodyBuilder();
            builder.part("file", message.getFileContent())
                    .filename(message.getFilename())
                    .contentType(MediaType.APPLICATION_PDF);

            FastApiUploadResponse fastApiResponse = ragServiceWebClient.post()
                    .uri("/documents/upload")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(FastApiUploadResponse.class)
                    .block();

            document.setVectorDocumentId(fastApiResponse.getDocumentId());
            document.setChunksIndexed(fastApiResponse.getChunksIndexed());
            document.setStatus(DocumentStatus.DONE);
        } catch (Exception e) {
            log.error("Xử lý document {} thất bại", document.getId(), e);
            document.setStatus(DocumentStatus.FAILED);
        }

        documentRepository.save(document);
    }

    public void delete(User owner, Long documentId) {
        Document document = documentRepository.findByIdAndOwner(documentId, owner)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                        "Không tìm thấy tài liệu hoặc bạn không có quyền xóa"));

        if (document.getVectorDocumentId() != null) {
            ragServiceWebClient.delete()
                    .uri("/documents/{id}", document.getVectorDocumentId())
                    .retrieve()
                    .toBodilessEntity()
                    .block();
        }

        documentRepository.delete(document);
    }

    public List<DocumentResponse> listMyDocuments(User owner) {
        return documentRepository.findByOwner(owner).stream()
                .map(this::toResponse)
                .toList();
    }

    private DocumentResponse toResponse(Document doc) {
        return DocumentResponse.builder()
                .id(doc.getId())
                .filename(doc.getFilename())
                .status(doc.getStatus())
                .chunksIndexed(doc.getChunksIndexed())
                .uploadedAt(doc.getUploadedAt())
                .build();
    }
}