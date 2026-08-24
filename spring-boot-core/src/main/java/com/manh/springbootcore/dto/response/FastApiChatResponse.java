package com.manh.springbootcore.dto.response;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter @Setter
public class FastApiChatResponse {
    private String answer;
    private List<SourceDto> sources;
}