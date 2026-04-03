package com.company.module.inventory.controller;

import com.company.module.inventory.dto.InventoryStorageRequestDto;
import com.company.module.inventory.dto.InventoryStorageResponseDto;
import com.company.module.inventory.service.InventoryStorageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Inventory Storage Location REST Controller.
 * URL API Prefix: /inventory-api/**
 * No @Transactional here - transactions are managed in Service layer only.
 */
@RestController
@RequestMapping("/inventory-api")
@RequiredArgsConstructor
public class InventoryStorageController {

    private final InventoryStorageService inventoryStorageService;

    // ============================================================
    // GET endpoints
    // ============================================================

    @GetMapping("/storage-locations")
    public ResponseEntity<List<InventoryStorageResponseDto>> findAll() {
        return ResponseEntity.ok(inventoryStorageService.findAll());
    }

    @GetMapping("/storage-locations/{id}")
    public ResponseEntity<InventoryStorageResponseDto> findById(@PathVariable Long id) {
        return ResponseEntity.ok(inventoryStorageService.findById(id));
    }

    @GetMapping("/storage-locations/code/{locationCode}")
    public ResponseEntity<InventoryStorageResponseDto> findByLocationCode(
            @PathVariable String locationCode) {
        return ResponseEntity.ok(inventoryStorageService.findByLocationCode(locationCode));
    }

    @GetMapping("/storage-locations/zone/{zone}")
    public ResponseEntity<List<InventoryStorageResponseDto>> findByZone(@PathVariable String zone) {
        return ResponseEntity.ok(inventoryStorageService.findByZone(zone));
    }

    @GetMapping("/storage-locations/available")
    public ResponseEntity<List<InventoryStorageResponseDto>> findAvailableLocations() {
        return ResponseEntity.ok(inventoryStorageService.findAvailableLocations());
    }

    // ============================================================
    // POST / PUT / DELETE endpoints
    // ============================================================

    @PostMapping("/storage-locations")
    public ResponseEntity<InventoryStorageResponseDto> create(
            @Valid @RequestBody InventoryStorageRequestDto requestDto) {
        InventoryStorageResponseDto created = inventoryStorageService.create(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/storage-locations/{id}")
    public ResponseEntity<InventoryStorageResponseDto> update(
            @PathVariable Long id,
            @Valid @RequestBody InventoryStorageRequestDto requestDto) {
        return ResponseEntity.ok(inventoryStorageService.update(id, requestDto));
    }

    @DeleteMapping("/storage-locations/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        inventoryStorageService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
