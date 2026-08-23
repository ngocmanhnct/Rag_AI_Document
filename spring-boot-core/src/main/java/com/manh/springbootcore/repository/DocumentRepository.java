package com.manh.springbootcore.repository;

import com.manh.springbootcore.entity.Document;
import com.manh.springbootcore.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DocumentRepository extends JpaRepository<Document, Long> {
    List<Document> findByOwner(User owner);
}