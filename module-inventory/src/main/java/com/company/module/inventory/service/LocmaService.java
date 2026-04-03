package com.company.module.inventory.service;

import com.company.module.inventory.dto.LocmaRequestDto;
import com.company.module.inventory.dto.LocmaResponseDto;
import com.company.module.inventory.entity.LocmaEntity;
import com.company.module.inventory.entity.LocmaId;
import com.company.module.inventory.repository.LocmaRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * LOCMA (Location Master) Service.
 * @Transactional is used ONLY at the Service layer.
 * Uses 'inventoryTransactionManager' for OracleDB.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class LocmaService {

    private final LocmaRepository locmaRepository;

    // ============================================================
    // READ
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findAll() {
        log.debug("Finding all LOCMA records");
        return locmaRepository.findAll().stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public LocmaResponseDto findById(Integer wareky, String locaky) {
        log.debug("Finding LOCMA by wareky={}, locaky={}", wareky, locaky);
        LocmaId id = new LocmaId(wareky, locaky);
        LocmaEntity entity = locmaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException(
                        "LOCMA not found: WAREKY=" + wareky + ", LOCAKY=" + locaky));
        return LocmaResponseDto.fromEntity(entity);
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findByWareky(Integer wareky) {
        log.debug("Finding LOCMA by wareky={}", wareky);
        return locmaRepository.findByWareky(wareky).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findByZoneky(String zoneky) {
        log.debug("Finding LOCMA by zoneky={}", zoneky);
        return locmaRepository.findByZoneky(zoneky).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findByWarekyAndZoneky(Integer wareky, String zoneky) {
        log.debug("Finding LOCMA by wareky={}, zoneky={}", wareky, zoneky);
        return locmaRepository.findByWarekyAndZoneky(wareky, zoneky).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findByAreaky(String areaky) {
        log.debug("Finding LOCMA by areaky={}", areaky);
        return locmaRepository.findByAreaky(areaky).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> findByStatus(Integer status) {
        log.debug("Finding LOCMA by status={}", status);
        return locmaRepository.findByStatus(status).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<LocmaResponseDto> searchByShortx(String keyword) {
        log.debug("Searching LOCMA by shortx keyword={}", keyword);
        return locmaRepository.searchByShortx(keyword).stream()
                .map(LocmaResponseDto::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(transactionManager = "inventoryTransactionManager", readOnly = true)
    public List<Map<String, Object>> countByWareky() {
        log.debug("Counting LOCMA by wareky");
        return locmaRepository.countByWareky().stream()
                .map(row -> Map.<String, Object>of("wareky", row[0], "count", row[1]))
                .collect(Collectors.toList());
    }

    // ============================================================
    // WRITE
    // ============================================================

    @Transactional(transactionManager = "inventoryTransactionManager")
    public LocmaResponseDto create(LocmaRequestDto dto) {
        log.info("Creating LOCMA: WAREKY={}, LOCAKY={}", dto.getWareky(), dto.getLocaky());

        LocmaId id = new LocmaId(dto.getWareky(), dto.getLocaky());
        if (locmaRepository.existsById(id)) {
            throw new IllegalArgumentException(
                    "LOCMA already exists: WAREKY=" + dto.getWareky() + ", LOCAKY=" + dto.getLocaky());
        }

        LocmaEntity entity = buildEntityFromDto(dto);
        LocmaEntity saved = locmaRepository.save(entity);
        log.info("LOCMA created successfully");
        return LocmaResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public LocmaResponseDto update(Integer wareky, String locaky, LocmaRequestDto dto) {
        log.info("Updating LOCMA: WAREKY={}, LOCAKY={}", wareky, locaky);

        LocmaId id = new LocmaId(wareky, locaky);
        LocmaEntity entity = locmaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException(
                        "LOCMA not found: WAREKY=" + wareky + ", LOCAKY=" + locaky));

        updateEntityFromDto(entity, dto);
        LocmaEntity saved = locmaRepository.save(entity);
        log.info("LOCMA updated successfully");
        return LocmaResponseDto.fromEntity(saved);
    }

    @Transactional(transactionManager = "inventoryTransactionManager")
    public void delete(Integer wareky, String locaky) {
        log.info("Deleting LOCMA: WAREKY={}, LOCAKY={}", wareky, locaky);

        LocmaId id = new LocmaId(wareky, locaky);
        if (!locmaRepository.existsById(id)) {
            throw new IllegalArgumentException(
                    "LOCMA not found: WAREKY=" + wareky + ", LOCAKY=" + locaky);
        }

        locmaRepository.deleteById(id);
        log.info("LOCMA deleted successfully");
    }

    // ============================================================
    // Private helpers
    // ============================================================

    private LocmaEntity buildEntityFromDto(LocmaRequestDto dto) {
        return LocmaEntity.builder()
                .wareky(dto.getWareky())
                .locaky(dto.getLocaky())
                .locaty(dto.getLocaty())
                .shortx(dto.getShortx())
                .taskty(dto.getTaskty())
                .zoneky(dto.getZoneky())
                .areaky(dto.getAreaky())
                .tkzone(dto.getTkzone())
                .faclty(dto.getFaclty())
                .arlvll(dto.getArlvll())
                .indcpc(dto.getIndcpc())
                .indtut(dto.getIndtut())
                .ibrout(dto.getIbrout())
                .obrout(dto.getObrout())
                .rprout(dto.getRprout())
                .status(dto.getStatus())
                .abcanv(dto.getAbcanv())
                .length(dto.getLength())
                .widthw(dto.getWidthw())
                .height(dto.getHeight())
                .cubicm(dto.getCubicm())
                .maxcpc(dto.getMaxcpc())
                .maxqty(dto.getMaxqty())
                .maxwgt(dto.getMaxwgt())
                .maxldr(dto.getMaxldr())
                .maxsec(dto.getMaxsec())
                .mixsku(dto.getMixsku())
                .mixlot(dto.getMixlot())
                .rpncat(dto.getRpncat())
                .indqtc(dto.getIndqtc())
                .qtychk(dto.getQtychk())
                .nedsid(dto.getNedsid())
                .indupa(dto.getIndupa())
                .indupk(dto.getIndupk())
                .autloc(dto.getAutloc())
                .credat(dto.getCredat())
                .cretim(dto.getCretim())
                .creusr(dto.getCreusr())
                .lmodat(dto.getLmodat())
                .lmotim(dto.getLmotim())
                .lmousr(dto.getLmousr())
                .indbzl(dto.getIndbzl())
                .indarc(dto.getIndarc())
                .updchk(dto.getUpdchk())
                .build();
    }

    private void updateEntityFromDto(LocmaEntity entity, LocmaRequestDto dto) {
        entity.setLocaty(dto.getLocaty());
        entity.setShortx(dto.getShortx());
        entity.setTaskty(dto.getTaskty());
        entity.setZoneky(dto.getZoneky());
        entity.setAreaky(dto.getAreaky());
        entity.setTkzone(dto.getTkzone());
        entity.setFaclty(dto.getFaclty());
        entity.setArlvll(dto.getArlvll());
        entity.setIndcpc(dto.getIndcpc());
        entity.setIndtut(dto.getIndtut());
        entity.setIbrout(dto.getIbrout());
        entity.setObrout(dto.getObrout());
        entity.setRprout(dto.getRprout());
        entity.setStatus(dto.getStatus());
        entity.setAbcanv(dto.getAbcanv());
        entity.setLength(dto.getLength());
        entity.setWidthw(dto.getWidthw());
        entity.setHeight(dto.getHeight());
        entity.setCubicm(dto.getCubicm());
        entity.setMaxcpc(dto.getMaxcpc());
        entity.setMaxqty(dto.getMaxqty());
        entity.setMaxwgt(dto.getMaxwgt());
        entity.setMaxldr(dto.getMaxldr());
        entity.setMaxsec(dto.getMaxsec());
        entity.setMixsku(dto.getMixsku());
        entity.setMixlot(dto.getMixlot());
        entity.setRpncat(dto.getRpncat());
        entity.setIndqtc(dto.getIndqtc());
        entity.setQtychk(dto.getQtychk());
        entity.setNedsid(dto.getNedsid());
        entity.setIndupa(dto.getIndupa());
        entity.setIndupk(dto.getIndupk());
        entity.setAutloc(dto.getAutloc());
        entity.setLmodat(dto.getLmodat());
        entity.setLmotim(dto.getLmotim());
        entity.setLmousr(dto.getLmousr());
        entity.setIndbzl(dto.getIndbzl());
        entity.setIndarc(dto.getIndarc());
        entity.setUpdchk(dto.getUpdchk());
    }
}
