package com.manh.springbootcore.dto.response;

import lombok.Builder;
import lombok.Getter;

@Getter @Builder
public class UserProfileResponse {
    private String email;
    private String fullName;
}