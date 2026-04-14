package com.company.module.inventory.service;

import com.company.module.inventory.dto.ZonmaRequestDto;
import com.company.module.inventory.dto.ZonmaResponseDto;
import com.company.module.inventory.entity.ZonmaEntity;
import com.company.module.inventory.entity.ZonmaId;
import com.company.module.inventory.repository.ZonmaRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * ZONMA (Zone Master) Service.
 * @Transactional is used ONLY at the Service layer.
 * Uses 'inventoryTransactionManager' for OracleDB.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ZonmaService {

    private final ZonmaRepository zonmaRepository;

    // ============================================================
    // READ
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findAll() {
        log.debug("Finding all ZONMA records");
        return zonmaRepository.findAll().stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public ZonmaResponseDto findById(Integer wareky, String zoneky) {
        log.debug("Finding ZONMA by wareky={}, zoneky={}", wareky, zoneky);
        ZonmaId id = new ZonmaId(wareky, zoneky);
        ZonmaEntity entity = zonmaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException(
                        "ZONMA not found: WAREKY=" + wareky + ", ZONEKY=" + zoneky));
        return ZonmaResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findByWareky(Integer wareky) {
        log.debug("Finding ZONMA by wareky={}", wareky);
        return zonmaRepository.findByWareky(wareky).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findByZonety(String zonety) {
        log.debug("Finding ZONMA by zonety={}", zonety);
        return zonmaRepository.findByZonety(zonety).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findByWarekyAndZonety(Integer wareky, String zonety) {
        log.debug("Finding ZONMA by wareky={}, zonety={}", wareky, zonety);
        return zonmaRepository.findByWarekyAndZonety(wareky, zonety).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findByAreaky(String areaky) {
        log.debug("Finding ZONMA by areaky={}", areaky);
        return zonmaRepository.findByAreaky(areaky).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> findByPlntky(String plntky) {
        log.debug("Finding ZONMA by plntky={}", plntky);
        return zonmaRepository.findByPlntky(plntky).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<ZonmaResponseDto> searchByShortx(String keyword) {
        log.debug("Searching ZONMA by shortx keyword={}", keyword);
        return zonmaRepository.searchByShortx(keyword).stream()
                .map(ZonmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<Map<String, Object>> countByWareky() {
        log.debug("Counting ZONMA by wareky");
        return zonmaRepository.countByWareky().stream()
                .map(row -> Map.<String, Object>of("wareky", row[0], "count", row[1]))
                .collect(Collectors.toList());
    }

    // ============================================================
    // WRITE
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager")
    public ZonmaResponseDto create(ZonmaRequestDto requestDto) {
        log.info("Creating ZONMA: WAREKY={}, ZONEKY={}", requestDto.getWareky(), requestDto.getZoneky());

        ZonmaId id = new ZonmaId(requestDto.getWareky(), requestDto.getZoneky());
        if (zonmaRepository.existsById(id)) {
            throw new IllegalArgumentException(
                    "ZONMA already exists: WAREKY=" + requestDto.getWareky()
                            + ", ZONEKY=" + requestDto.getZoneky());
        }

        ZonmaEntity entity = ZonmaEntity.builder()
                .wareky(requestDto.getWareky())
                .zoneky(requestDto.getZoneky())
                .zonety(requestDto.getZonety())
                .shortx(requestDto.getShortx())
                .areaky(requestDto.getAreaky())
                .credat(requestDto.getCredat())
                .cretim(requestDto.getCretim())
                .creusr(requestDto.getCreusr())
                .lmodat(requestDto.getLmodat())
                .lmotim(requestDto.getLmotim())
                .lmousr(requestDto.getLmousr())
                .indbzl(requestDto.getIndbzl())
                .indarc(requestDto.getIndarc())
                .updchk(requestDto.getUpdchk())
                .plntky(requestDto.getPlntky())
                .stlky(requestDto.getStlky())
                .build();

        ZonmaEntity saved = zonmaRepository.save(entity);
        log.info("ZONMA created successfully");
        return ZonmaResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public ZonmaResponseDto update(Integer wareky, String zoneky, ZonmaRequestDto requestDto) {
        log.info("Updating ZONMA: WAREKY={}, ZONEKY={}", wareky, zoneky);

        ZonmaId id = new ZonmaId(wareky, zoneky);
        ZonmaEntity entity = zonmaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException(
                        "ZONMA not found: WAREKY=" + wareky + ", ZONEKY=" + zoneky));

        entity.setZonety(requestDto.getZonety());
        entity.setShortx(requestDto.getShortx());
        entity.setAreaky(requestDto.getAreaky());
        entity.setLmodat(requestDto.getLmodat());
        entity.setLmotim(requestDto.getLmotim());
        entity.setLmousr(requestDto.getLmousr());
        entity.setIndbzl(requestDto.getIndbzl());
        entity.setIndarc(requestDto.getIndarc());
        entity.setUpdchk(requestDto.getUpdchk());
        entity.setPlntky(requestDto.getPlntky());
        entity.setStlky(requestDto.getStlky());

        ZonmaEntity saved = zonmaRepository.save(entity);
        log.info("ZONMA updated successfully");
        return ZonmaResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public void delete(Integer wareky, String zoneky) {
        log.info("Deleting ZONMA: WAREKY={}, ZONEKY={}", wareky, zoneky);

        ZonmaId id = new ZonmaId(wareky, zoneky);
        if (!zonmaRepository.existsById(id)) {
            throw new IllegalArgumentException(
                    "ZONMA not found: WAREKY=" + wareky + ", ZONEKY=" + zoneky);
        }

        zonmaRepository.deleteById(id);
        log.info("ZONMA deleted successfully");
    }
}
