package org.opensw.kiosk.service;

import lombok.Builder;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.opensw.kiosk.entity.Menu;
import org.opensw.kiosk.repository.KioskRepository;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
@Log4j2
public class KioskServiceImpl implements KioskService {

    private final KioskRepository kioskRepository;

    @Override
    public List<Menu> getAllKiosks() {
        return kioskRepository.findAll();
    }

    @Override
    public String readFileFromClassPath(String filename) throws IOException {
        ClassPathResource resource = new ClassPathResource(filename); // 클래스패스 기준
        Path path = resource.getFile().toPath();
        return Files.readString(path); // 파일 내용 읽기
    }
}
