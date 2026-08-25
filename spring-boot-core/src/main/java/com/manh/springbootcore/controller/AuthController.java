package com.manh.springbootcore.controller;

import com.manh.springbootcore.dto.request.ChangePasswordRequest;
import com.manh.springbootcore.dto.request.UpdateProfileRequest;
import com.manh.springbootcore.dto.response.AuthResponse;
import com.manh.springbootcore.dto.request.LoginRequest;
import com.manh.springbootcore.dto.request.RegisterRequest;
import com.manh.springbootcore.dto.response.UserProfileResponse;
import com.manh.springbootcore.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import com.manh.springbootcore.entity.User;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public AuthResponse register(@Valid @RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request);
    }
    @GetMapping("/me")
    public String me(@AuthenticationPrincipal User user) {
        return "Xin chào " + user.getFullName() + ", email: " + user.getEmail();
    }
    @PostMapping("/change-password")
    public void changePassword(@AuthenticationPrincipal User currentUser,
                               @Valid @RequestBody ChangePasswordRequest request) {
        authService.changePassword(currentUser, request);
    }
    @PutMapping("/profile")
    public UserProfileResponse updateProfile(@AuthenticationPrincipal User currentUser,
                                             @Valid @RequestBody UpdateProfileRequest request) {
        return authService.updateProfile(currentUser, request);
    }
}
