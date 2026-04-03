package com.company.module.inventory.service;

import com.company.module.inventory.dto.ZonmaRequestDto;
import com.company.module.inventory.dto.ZonmaResponseDto;
import com.company.module.inventory.entity.ZonmaEntity;
import com.company.module.inventory.entity.ZonmaId;
import com.company.module.inventory.repository.ZonmaRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("ZonmaService Unit Tests")
class ZonmaServiceTest {

    @Mock
    private ZonmaRepository zonmaRepository;

    @InjectMocks
    private ZonmaService zonmaService;

    private ZonmaEntity sampleEntity;
    private ZonmaRequestDto sampleRequest;

    @BeforeEach
    void setUp() {
        sampleEntity = ZonmaEntity.builder()
                .wareky(1100)
                .zoneky("RCV")
                .zonety("RECV")
                .shortx("입하장")
                .areaky("RCV")
                .credat(20220103)
                .cretim(0)
                .creusr("HNW")
                .lmodat(20220103)
                .lmotim(0)
                .lmousr("HNW")
                .indbzl(" ")
                .indarc(" ")
                .updchk(0)
                .plntky(" ")
                .stlky(" ")
                .build();

        sampleRequest = ZonmaRequestDto.builder()
                .wareky(1100)
                .zoneky("RCV")
                .zonety("RECV")
                .shortx("입하장")
                .areaky("RCV")
                .credat(20220103)
                .cretim(0)
                .creusr("HNW")
                .lmodat(20220103)
                .lmotim(0)
                .lmousr("HNW")
                .build();
    }

    @Test
    @DisplayName("전체 ZONMA 조회")
    void findAll_ShouldReturnAll() {
        when(zonmaRepository.findAll()).thenReturn(Arrays.asList(sampleEntity));

        List<ZonmaResponseDto> result = zonmaService.findAll();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getWareky()).isEqualTo(1100);
        assertThat(result.get(0).getZoneky()).isEqualTo("RCV");
    }

    @Test
    @DisplayName("복합키(WAREKY+ZONEKY) 단건 조회")
    void findById_ShouldReturnEntity() {
        ZonmaId id = new ZonmaId(1100, "RCV");
        when(zonmaRepository.findById(id)).thenReturn(Optional.of(sampleEntity));

        ZonmaResponseDto result = zonmaService.findById(1100, "RCV");

        assertThat(result.getWareky()).isEqualTo(1100);
        assertThat(result.getZoneky()).isEqualTo("RCV");
        assertThat(result.getShortx()).isEqualTo("입하장");
    }

    @Test
    @DisplayName("존재하지 않는 ZONMA 조회 시 예외")
    void findById_ShouldThrow_WhenNotFound() {
        ZonmaId id = new ZonmaId(9999, "XXX");
        when(zonmaRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> zonmaService.findById(9999, "XXX"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("ZONMA not found");
    }

    @Test
    @DisplayName("거점(WAREKY) 기준 조회")
    void findByWareky_ShouldReturnList() {
        when(zonmaRepository.findByWareky(1100)).thenReturn(Arrays.asList(sampleEntity));

        List<ZonmaResponseDto> result = zonmaService.findByWareky(1100);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getWareky()).isEqualTo(1100);
    }

    @Test
    @DisplayName("타입(ZONETY) 기준 조회")
    void findByZonety_ShouldReturnList() {
        when(zonmaRepository.findByZonety("RECV")).thenReturn(Arrays.asList(sampleEntity));

        List<ZonmaResponseDto> result = zonmaService.findByZonety("RECV");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getZonety()).isEqualTo("RECV");
    }

    @Test
    @DisplayName("신규 ZONMA 등록")
    void create_ShouldCreateEntity() {
        when(zonmaRepository.existsById(any(ZonmaId.class))).thenReturn(false);
        when(zonmaRepository.save(any(ZonmaEntity.class))).thenReturn(sampleEntity);

        ZonmaResponseDto result = zonmaService.create(sampleRequest);

        assertThat(result.getWareky()).isEqualTo(1100);
        assertThat(result.getZoneky()).isEqualTo("RCV");
        verify(zonmaRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("중복 ZONMA 등록 시 예외")
    void create_ShouldThrow_WhenDuplicate() {
        when(zonmaRepository.existsById(any(ZonmaId.class))).thenReturn(true);

        assertThatThrownBy(() -> zonmaService.create(sampleRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("already exists");
    }

    @Test
    @DisplayName("ZONMA 수정")
    void update_ShouldUpdateEntity() {
        ZonmaId id = new ZonmaId(1100, "RCV");
        when(zonmaRepository.findById(id)).thenReturn(Optional.of(sampleEntity));
        when(zonmaRepository.save(any(ZonmaEntity.class))).thenReturn(sampleEntity);

        ZonmaResponseDto result = zonmaService.update(1100, "RCV", sampleRequest);

        assertThat(result).isNotNull();
        verify(zonmaRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("ZONMA 삭제")
    void delete_ShouldDeleteEntity() {
        ZonmaId id = new ZonmaId(1100, "RCV");
        when(zonmaRepository.existsById(id)).thenReturn(true);
        doNothing().when(zonmaRepository).deleteById(id);

        zonmaService.delete(1100, "RCV");

        verify(zonmaRepository, times(1)).deleteById(id);
    }

    @Test
    @DisplayName("명칭 키워드 검색")
    void searchByShortx_ShouldReturnMatching() {
        when(zonmaRepository.searchByShortx("입하")).thenReturn(Arrays.asList(sampleEntity));

        List<ZonmaResponseDto> result = zonmaService.searchByShortx("입하");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getShortx()).contains("입하");
    }
}
