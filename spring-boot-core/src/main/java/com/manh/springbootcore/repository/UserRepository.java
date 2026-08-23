package com.manh.springbootcore.repository;

import com.manh.springbootcore.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);   // Spring Data JPA tự sinh câu SQL từ tên hàm này
}