package com.manh.springbootcore.repository;

import com.manh.springbootcore.entity.ChatMessage;
import com.manh.springbootcore.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {
    List<ChatMessage> findByOwnerOrderByCreatedAtDesc(User owner);
}