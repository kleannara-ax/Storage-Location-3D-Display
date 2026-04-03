package com.company.module.inventory.repository;

import com.company.module.inventory.entity.InventoryItemEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface InventoryItemRepository extends JpaRepository<InventoryItemEntity, Long> {

    Optional<InventoryItemEntity> findByItemCode(String itemCode);

    List<InventoryItemEntity> findByCategory(String category);

    List<InventoryItemEntity> findByUseYn(String useYn);

    List<InventoryItemEntity> findByStorageLocation(String storageLocation);

    @Query("SELECT i FROM InventoryItemEntity i WHERE i.itemName LIKE %:keyword% AND i.useYn = 'Y'")
    List<InventoryItemEntity> searchByItemName(@Param("keyword") String keyword);

    @Query("SELECT i FROM InventoryItemEntity i WHERE i.quantity <= :threshold AND i.useYn = 'Y'")
    List<InventoryItemEntity> findLowStockItems(@Param("threshold") int threshold);

    boolean existsByItemCode(String itemCode);
}
