package com.manh.springbootcore.service;

import com.manh.springbootcore.dto.response.DocumentResponse;
import com.manh.springbootcore.dto.response.FastApiUploadResponse;
import com.manh.springbootcore.entity.Document;
import com.manh.springbootcore.entity.User;
import com.manh.springbootcore.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
@RequiredArgsConstructor
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final WebClient ragServiceWebClient;

    public DocumentResponse upload(User owner, MultipartFile file) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", file.getResource())
                .filename(file.getOriginalFilename());

        FastApiUploadResponse fastApiResponse = ragServiceWebClient.post()
                .uri("/documents/upload")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(FastApiUploadResponse.class)
                .block();

        Document document = Document.builder()
                .filename(file.getOriginalFilename())
                .vectorDocumentId(fastApiResponse.getDocumentId())
                .chunksIndexed(fastApiResponse.getChunksIndexed())
                .owner(owner)
                .build();

        documentRepository.save(document);

        return DocumentResponse.builder()
                .id(document.getId())
                .filename(document.getFilename())
                .chunksIndexed(document.getChunksIndexed())
                .uploadedAt(document.getUploadedAt())
                .build();
    }
    public List<DocumentResponse> listMyDocuments(User owner) {
        return documentRepository.findByOwner(owner).stream()
                .map(doc -> DocumentResponse.builder()
                        .id(doc.getId())
                        .filename(doc.getFilename())
                        .chunksIndexed(doc.getChunksIndexed())
                        .uploadedAt(doc.getUploadedAt())
                        .build())
                .toList();
    }
    public void delete(User owner, Long documentId) {
        Document document = documentRepository.findByIdAndOwner(documentId, owner)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                        "Không tìm thấy tài liệu hoặc bạn không có quyền xóa"));

        ragServiceWebClient.delete()
                .uri("/documents/{id}", document.getVectorDocumentId())
                .retrieve()
                .toBodilessEntity()
                .block();

        documentRepository.delete(document);
    }
}