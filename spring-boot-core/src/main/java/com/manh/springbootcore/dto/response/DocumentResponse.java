package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter @Builder
public class DocumentResponse {
    private Long id;
    private String filename;
    private Integer chunksIndexed;
    private LocalDateTime uploadedAt;
}