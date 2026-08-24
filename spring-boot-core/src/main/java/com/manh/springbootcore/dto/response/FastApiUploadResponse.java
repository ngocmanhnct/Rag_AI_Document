package com.manh.springbootcore.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class FastApiUploadResponse {

    @JsonProperty("document_id")
    private String documentId;

    private String filename;

    @JsonProperty("chunks_indexed")
    private Integer chunksIndexed;
}