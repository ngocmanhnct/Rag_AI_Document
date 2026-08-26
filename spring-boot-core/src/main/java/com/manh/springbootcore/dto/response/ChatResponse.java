package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.io.Serializable;
import java.util.List;

@Getter @Builder
public class ChatResponse implements Serializable {
    private String answer;
    private List<SourceDto> sources;
}