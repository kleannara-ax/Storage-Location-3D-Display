package com.company.module.inventory.repository;

import com.company.module.inventory.entity.InventoryStorageEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface InventoryStorageRepository extends JpaRepository<InventoryStorageEntity, Long> {

    Optional<InventoryStorageEntity> findByLocationCode(String locationCode);

    List<InventoryStorageEntity> findByZone(String zone);

    List<InventoryStorageEntity> findByUseYn(String useYn);

    @Query("SELECT s FROM InventoryStorageEntity s WHERE s.currentUsage < s.capacity AND s.useYn = 'Y'")
    List<InventoryStorageEntity> findAvailableLocations();

    @Query("SELECT s FROM InventoryStorageEntity s WHERE s.zone = :zone AND s.useYn = 'Y' ORDER BY s.locationCode")
    List<InventoryStorageEntity> findActiveLocationsByZone(@Param("zone") String zone);

    boolean existsByLocationCode(String locationCode);
}
