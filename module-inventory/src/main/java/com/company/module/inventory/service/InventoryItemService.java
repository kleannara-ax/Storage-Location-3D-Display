package com.company.module.inventory.service;

import com.company.module.inventory.dto.InventoryItemRequestDto;
import com.company.module.inventory.dto.InventoryItemResponseDto;
import com.company.module.inventory.entity.InventoryItemEntity;
import com.company.module.inventory.repository.InventoryItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Inventory Item Service.
 * @Transactional is used ONLY at the Service layer as per project conventions.
 * Uses 'inventoryTransactionManager' for OracleDB transactions.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class InventoryItemService {

    private final InventoryItemRepository inventoryItemRepository;

    // ============================================================
    // READ operations (readOnly = true)
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryItemResponseDto> findAll() {
        log.debug("Finding all inventory items");
        return inventoryItemRepository.findAll().stream()
                .map(InventoryItemResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public InventoryItemResponseDto findById(Long id) {
        log.debug("Finding inventory item by id: {}", id);
        InventoryItemEntity entity = inventoryItemRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Inventory item not found with id: " + id));
        return InventoryItemResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public InventoryItemResponseDto findByItemCode(String itemCode) {
        log.debug("Finding inventory item by code: {}", itemCode);
        InventoryItemEntity entity = inventoryItemRepository.findByItemCode(itemCode)
                .orElseThrow(() -> new IllegalArgumentException("Inventory item not found with code: " + itemCode));
        return InventoryItemResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryItemResponseDto> findByCategory(String category) {
        log.debug("Finding inventory items by category: {}", category);
        return inventoryItemRepository.findByCategory(category).stream()
                .map(InventoryItemResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryItemResponseDto> searchByItemName(String keyword) {
        log.debug("Searching inventory items by keyword: {}", keyword);
        return inventoryItemRepository.searchByItemName(keyword).stream()
                .map(InventoryItemResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryItemResponseDto> findLowStockItems(int threshold) {
        log.debug("Finding low stock items with threshold: {}", threshold);
        return inventoryItemRepository.findLowStockItems(threshold).stream()
                .map(InventoryItemResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    // ============================================================
    // WRITE operations
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager")
    public InventoryItemResponseDto create(InventoryItemRequestDto requestDto) {
        log.info("Creating inventory item: {}", requestDto.getItemCode());

        if (inventoryItemRepository.existsByItemCode(requestDto.getItemCode())) {
            throw new IllegalArgumentException("Item code already exists: " + requestDto.getItemCode());
        }

        InventoryItemEntity entity = InventoryItemEntity.builder()
                .itemCode(requestDto.getItemCode())
                .itemName(requestDto.getItemName())
                .category(requestDto.getCategory())
                .quantity(requestDto.getQuantity())
                .unitPrice(requestDto.getUnitPrice())
                .storageLocation(requestDto.getStorageLocation())
                .description(requestDto.getDescription())
                .build();

        InventoryItemEntity saved = inventoryItemRepository.save(entity);
        log.info("Inventory item created successfully: {}", saved.getItemId());

        return InventoryItemResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public InventoryItemResponseDto update(Long id, InventoryItemRequestDto requestDto) {
        log.info("Updating inventory item: {}", id);

        InventoryItemEntity entity = inventoryItemRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Inventory item not found with id: " + id));

        entity.setItemName(requestDto.getItemName());
        entity.setCategory(requestDto.getCategory());
        entity.setQuantity(requestDto.getQuantity());
        entity.setUnitPrice(requestDto.getUnitPrice());
        entity.setStorageLocation(requestDto.getStorageLocation());
        entity.setDescription(requestDto.getDescription());

        InventoryItemEntity saved = inventoryItemRepository.save(entity);
        log.info("Inventory item updated successfully: {}", saved.getItemId());

        return InventoryItemResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public void delete(Long id) {
        log.info("Soft-deleting inventory item: {}", id);

        InventoryItemEntity entity = inventoryItemRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Inventory item not found with id: " + id));

        entity.setUseYn("N");
        inventoryItemRepository.save(entity);
        log.info("Inventory item soft-deleted successfully: {}", id);
    }
}
