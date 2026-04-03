package com.company.module.user.controller;

import com.company.module.user.entity.UserEntity;
import com.company.module.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user-api")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/users")
    public ResponseEntity<List<UserEntity>> findAll() {
        return ResponseEntity.ok(userService.findAll());
    }

    @GetMapping("/users/{id}")
    public ResponseEntity<UserEntity> findById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }
}
