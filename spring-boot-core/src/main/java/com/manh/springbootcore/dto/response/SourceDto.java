package com.manh.springbootcore.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class SourceDto {
    private String filename;

    @JsonProperty("chunk_index")
    private Integer chunkIndex;

    private Double score;
}