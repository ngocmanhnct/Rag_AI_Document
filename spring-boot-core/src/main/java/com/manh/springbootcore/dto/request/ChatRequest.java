package com.manh.springbootcore.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class ChatRequest {

    @NotBlank(message = "Câu hỏi không được để trống")
    private String query;
}