package com.manh.springbootcore.controller;

import com.manh.springbootcore.dto.response.DocumentResponse;
import com.manh.springbootcore.entity.User;
import com.manh.springbootcore.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/documents")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @PostMapping(value = "/upload", consumes = "multipart/form-data")
    public DocumentResponse upload(@AuthenticationPrincipal User currentUser,
                                   @RequestParam("file") MultipartFile file) {
        return documentService.upload(currentUser, file);
    }
    @GetMapping
    public List<DocumentResponse> list(@AuthenticationPrincipal User currentUser) {
        return documentService.listMyDocuments(currentUser);
    }
    @DeleteMapping("/{id}")
    public void delete(@AuthenticationPrincipal User currentUser, @PathVariable Long id) {
        documentService.delete(currentUser, id);
    }
}