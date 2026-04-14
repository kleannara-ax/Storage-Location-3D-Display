package com.company.module.inventory.service;

import com.company.module.inventory.dto.InventoryStorageRequestDto;
import com.company.module.inventory.dto.InventoryStorageResponseDto;
import com.company.module.inventory.entity.InventoryStorageEntity;
import com.company.module.inventory.repository.InventoryStorageRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Inventory Storage Location Service.
 * @Transactional is used ONLY at the Service layer as per project conventions.
 * Uses 'inventoryTransactionManager' for OracleDB transactions.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class InventoryStorageService {

    private final InventoryStorageRepository inventoryStorageRepository;

    // ============================================================
    // READ operations
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryStorageResponseDto> findAll() {
        log.debug("Finding all storage locations");
        return inventoryStorageRepository.findAll().stream()
                .map(InventoryStorageResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public InventoryStorageResponseDto findById(Long id) {
        log.debug("Finding storage location by id: {}", id);
        InventoryStorageEntity entity = inventoryStorageRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Storage location not found with id: " + id));
        return InventoryStorageResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public InventoryStorageResponseDto findByLocationCode(String locationCode) {
        log.debug("Finding storage location by code: {}", locationCode);
        InventoryStorageEntity entity = inventoryStorageRepository.findByLocationCode(locationCode)
                .orElseThrow(() -> new IllegalArgumentException(
                        "Storage location not found with code: " + locationCode));
        return InventoryStorageResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryStorageResponseDto> findByZone(String zone) {
        log.debug("Finding storage locations by zone: {}", zone);
        return inventoryStorageRepository.findActiveLocationsByZone(zone).stream()
                .map(InventoryStorageResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<InventoryStorageResponseDto> findAvailableLocations() {
        log.debug("Finding available storage locations");
        return inventoryStorageRepository.findAvailableLocations().stream()
                .map(InventoryStorageResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    // ============================================================
    // WRITE operations
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager")
    public InventoryStorageResponseDto create(InventoryStorageRequestDto requestDto) {
        log.info("Creating storage location: {}", requestDto.getLocationCode());

        if (inventoryStorageRepository.existsByLocationCode(requestDto.getLocationCode())) {
            throw new IllegalArgumentException(
                    "Location code already exists: " + requestDto.getLocationCode());
        }

        InventoryStorageEntity entity = InventoryStorageEntity.builder()
                .locationCode(requestDto.getLocationCode())
                .locationName(requestDto.getLocationName())
                .zone(requestDto.getZone())
                .coordX(requestDto.getCoordX())
                .coordY(requestDto.getCoordY())
                .coordZ(requestDto.getCoordZ())
                .capacity(requestDto.getCapacity())
                .build();

        InventoryStorageEntity saved = inventoryStorageRepository.save(entity);
        log.info("Storage location created successfully: {}", saved.getLocationId());

        return InventoryStorageResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public InventoryStorageResponseDto update(Long id, InventoryStorageRequestDto requestDto) {
        log.info("Updating storage location: {}", id);

        InventoryStorageEntity entity = inventoryStorageRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Storage location not found with id: " + id));

        entity.setLocationName(requestDto.getLocationName());
        entity.setZone(requestDto.getZone());
        entity.setCoordX(requestDto.getCoordX());
        entity.setCoordY(requestDto.getCoordY());
        entity.setCoordZ(requestDto.getCoordZ());
        entity.setCapacity(requestDto.getCapacity());

        InventoryStorageEntity saved = inventoryStorageRepository.save(entity);
        log.info("Storage location updated successfully: {}", saved.getLocationId());

        return InventoryStorageResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public void delete(Long id) {
        log.info("Soft-deleting storage location: {}", id);

        InventoryStorageEntity entity = inventoryStorageRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Storage location not found with id: " + id));

        entity.setUseYn("N");
        inventoryStorageRepository.save(entity);
        log.info("Storage location soft-deleted successfully: {}", id);
    }
}
