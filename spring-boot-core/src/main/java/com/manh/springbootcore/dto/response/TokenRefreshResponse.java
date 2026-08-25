package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;

@Getter @Builder
public class TokenRefreshResponse {
    private String token;
    private String refreshToken;
}