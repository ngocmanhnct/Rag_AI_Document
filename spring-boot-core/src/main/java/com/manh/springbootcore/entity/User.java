package com.manh.springbootcore.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import java.util.Collection;
import java.util.List;

@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class User implements UserDetails {   // implements UserDetails để Spring Security hiểu được entity này

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;   // sẽ lưu password ĐÃ HASH, không bao giờ lưu plain text

    private String fullName;

    // ---- Các phương thức bắt buộc phải override vì implements UserDetails ----
    // Đây là "hợp đồng" Spring Security yêu cầu để biết cách xử lý user này

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_USER")); // đơn giản hóa: ai cũng là USER
    }

    @Override
    public String getUsername() {
        return email;   // ta dùng email làm "username" đăng nhập
    }

    @Override
    public boolean isAccountNonExpired() { return true; }
    @Override
    public boolean isAccountNonLocked() { return true; }
    @Override
    public boolean isCredentialsNonExpired() { return true; }
    @Override
    public boolean isEnabled() { return true; }
}