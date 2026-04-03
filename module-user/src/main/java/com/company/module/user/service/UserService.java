package com.company.module.user.service;

import com.company.module.user.entity.UserEntity;
import com.company.module.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public List<UserEntity> findAll() {
        return userRepository.findAll();
    }

    @Transactional(readOnly = true)
    public UserEntity findById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("User not found with id: " + id));
    }

    @Transactional
    public UserEntity save(UserEntity user) {
        log.info("Saving user: {}", user.getUsername());
        return userRepository.save(user);
    }
}
