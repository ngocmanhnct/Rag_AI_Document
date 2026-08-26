package com.manh.springbootcore.dto.response;

import com.manh.springbootcore.entity.DocumentStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter @Builder
public class DocumentResponse {
    private Long id;
    private String filename;
    private DocumentStatus status;
    private Integer chunksIndexed;
    private LocalDateTime uploadedAt;
}