package com.company.module.inventory.service;

import com.company.module.inventory.dto.InventoryItemRequestDto;
import com.company.module.inventory.dto.InventoryItemResponseDto;
import com.company.module.inventory.entity.InventoryItemEntity;
import com.company.module.inventory.repository.InventoryItemRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("InventoryItemService Unit Tests")
class InventoryItemServiceTest {

    @Mock
    private InventoryItemRepository inventoryItemRepository;

    @InjectMocks
    private InventoryItemService inventoryItemService;

    private InventoryItemEntity sampleEntity;
    private InventoryItemRequestDto sampleRequest;

    @BeforeEach
    void setUp() {
        sampleEntity = InventoryItemEntity.builder()
                .itemId(1L)
                .itemCode("ITM-TEST-001")
                .itemName("Test Item")
                .category("TEST")
                .quantity(100)
                .unitPrice(new BigDecimal("25.50"))
                .storageLocation("LOC-A01-01")
                .description("Test item description")
                .useYn("Y")
                .build();

        sampleRequest = InventoryItemRequestDto.builder()
                .itemCode("ITM-TEST-001")
                .itemName("Test Item")
                .category("TEST")
                .quantity(100)
                .unitPrice(new BigDecimal("25.50"))
                .storageLocation("LOC-A01-01")
                .description("Test item description")
                .build();
    }

    @Test
    @DisplayName("Should return all inventory items")
    void findAll_ShouldReturnAllItems() {
        // given
        when(inventoryItemRepository.findAll()).thenReturn(Arrays.asList(sampleEntity));

        // when
        List<InventoryItemResponseDto> result = inventoryItemService.findAll();

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getItemCode()).isEqualTo("ITM-TEST-001");
        verify(inventoryItemRepository, times(1)).findAll();
    }

    @Test
    @DisplayName("Should return item by ID")
    void findById_ShouldReturnItem() {
        // given
        when(inventoryItemRepository.findById(1L)).thenReturn(Optional.of(sampleEntity));

        // when
        InventoryItemResponseDto result = inventoryItemService.findById(1L);

        // then
        assertThat(result.getItemId()).isEqualTo(1L);
        assertThat(result.getItemCode()).isEqualTo("ITM-TEST-001");
    }

    @Test
    @DisplayName("Should throw exception when item not found by ID")
    void findById_ShouldThrowException_WhenNotFound() {
        // given
        when(inventoryItemRepository.findById(999L)).thenReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> inventoryItemService.findById(999L))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Inventory item not found with id: 999");
    }

    @Test
    @DisplayName("Should create new inventory item")
    void create_ShouldCreateItem() {
        // given
        when(inventoryItemRepository.existsByItemCode(anyString())).thenReturn(false);
        when(inventoryItemRepository.save(any(InventoryItemEntity.class))).thenReturn(sampleEntity);

        // when
        InventoryItemResponseDto result = inventoryItemService.create(sampleRequest);

        // then
        assertThat(result.getItemCode()).isEqualTo("ITM-TEST-001");
        assertThat(result.getQuantity()).isEqualTo(100);
        verify(inventoryItemRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("Should throw exception when creating item with duplicate code")
    void create_ShouldThrowException_WhenDuplicateCode() {
        // given
        when(inventoryItemRepository.existsByItemCode("ITM-TEST-001")).thenReturn(true);

        // when & then
        assertThatThrownBy(() -> inventoryItemService.create(sampleRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Item code already exists");
    }

    @Test
    @DisplayName("Should update existing inventory item")
    void update_ShouldUpdateItem() {
        // given
        when(inventoryItemRepository.findById(1L)).thenReturn(Optional.of(sampleEntity));
        when(inventoryItemRepository.save(any(InventoryItemEntity.class))).thenReturn(sampleEntity);

        sampleRequest.setItemName("Updated Item Name");

        // when
        InventoryItemResponseDto result = inventoryItemService.update(1L, sampleRequest);

        // then
        assertThat(result).isNotNull();
        verify(inventoryItemRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("Should soft-delete inventory item")
    void delete_ShouldSoftDeleteItem() {
        // given
        when(inventoryItemRepository.findById(1L)).thenReturn(Optional.of(sampleEntity));
        when(inventoryItemRepository.save(any(InventoryItemEntity.class))).thenReturn(sampleEntity);

        // when
        inventoryItemService.delete(1L);

        // then
        assertThat(sampleEntity.getUseYn()).isEqualTo("N");
        verify(inventoryItemRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("Should search items by keyword")
    void searchByItemName_ShouldReturnMatchingItems() {
        // given
        when(inventoryItemRepository.searchByItemName("Test"))
                .thenReturn(Arrays.asList(sampleEntity));

        // when
        List<InventoryItemResponseDto> result = inventoryItemService.searchByItemName("Test");

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getItemName()).contains("Test");
    }

    @Test
    @DisplayName("Should find low stock items")
    void findLowStockItems_ShouldReturnLowStockItems() {
        // given
        InventoryItemEntity lowStockEntity = InventoryItemEntity.builder()
                .itemId(2L)
                .itemCode("ITM-LOW-001")
                .itemName("Low Stock Item")
                .quantity(3)
                .useYn("Y")
                .build();

        when(inventoryItemRepository.findLowStockItems(10))
                .thenReturn(Arrays.asList(lowStockEntity));

        // when
        List<InventoryItemResponseDto> result = inventoryItemService.findLowStockItems(10);

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getQuantity()).isLessThanOrEqualTo(10);
    }
}
