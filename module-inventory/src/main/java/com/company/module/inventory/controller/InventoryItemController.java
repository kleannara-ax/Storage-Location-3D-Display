package com.company.module.inventory.controller;

import com.company.module.inventory.dto.InventoryItemRequestDto;
import com.company.module.inventory.dto.InventoryItemResponseDto;
import com.company.module.inventory.service.InventoryItemService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Inventory Item REST Controller.
 * URL API Prefix: /inventory-api/**
 * No @Transactional here - transactions are managed in Service layer only.
 */
@RestController
@RequestMapping("/inventory-api")
@RequiredArgsConstructor
public class InventoryItemController {

    private final InventoryItemService inventoryItemService;

    // ============================================================
    // GET endpoints
    // ============================================================

    @GetMapping("/items")
    public ResponseEntity<List<InventoryItemResponseDto>> findAll() {
        return ResponseEntity.ok(inventoryItemService.findAll());
    }

    @GetMapping("/items/{id}")
    public ResponseEntity<InventoryItemResponseDto> findById(@PathVariable Long id) {
        return ResponseEntity.ok(inventoryItemService.findById(id));
    }

    @GetMapping("/items/code/{itemCode}")
    public ResponseEntity<InventoryItemResponseDto> findByItemCode(@PathVariable String itemCode) {
        return ResponseEntity.ok(inventoryItemService.findByItemCode(itemCode));
    }

    @GetMapping("/items/category/{category}")
    public ResponseEntity<List<InventoryItemResponseDto>> findByCategory(@PathVariable String category) {
        return ResponseEntity.ok(inventoryItemService.findByCategory(category));
    }

    @GetMapping("/items/search")
    public ResponseEntity<List<InventoryItemResponseDto>> searchByItemName(
            @RequestParam String keyword) {
        return ResponseEntity.ok(inventoryItemService.searchByItemName(keyword));
    }

    @GetMapping("/items/low-stock")
    public ResponseEntity<List<InventoryItemResponseDto>> findLowStockItems(
            @RequestParam(defaultValue = "10") int threshold) {
        return ResponseEntity.ok(inventoryItemService.findLowStockItems(threshold));
    }

    // ============================================================
    // POST / PUT / DELETE endpoints
    // ============================================================

    @PostMapping("/items")
    public ResponseEntity<InventoryItemResponseDto> create(
            @Valid @RequestBody InventoryItemRequestDto requestDto) {
        InventoryItemResponseDto created = inventoryItemService.create(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/items/{id}")
    public ResponseEntity<InventoryItemResponseDto> update(
            @PathVariable Long id,
            @Valid @RequestBody InventoryItemRequestDto requestDto) {
        return ResponseEntity.ok(inventoryItemService.update(id, requestDto));
    }

    @DeleteMapping("/items/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        inventoryItemService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
