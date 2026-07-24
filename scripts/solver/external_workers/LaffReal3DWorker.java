import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

import com.github.skjolber.packing.api.Box;
import com.github.skjolber.packing.api.BoxItem;
import com.github.skjolber.packing.api.BoxStackValue;
import com.github.skjolber.packing.api.Container;
import com.github.skjolber.packing.api.ContainerItem;
import com.github.skjolber.packing.api.PackagerResult;
import com.github.skjolber.packing.api.Placement;
import com.github.skjolber.packing.packer.laff.LargestAreaFitFirstPackager;

public final class LaffReal3DWorker {
    private static final String INPUT_HEADER = "P64L08REAL3D\t1";
    private static final String OUTPUT_HEADER = "P64L08REAL3DRESULT\t1";

    private static String decode(String value) {
        int padding = (4 - value.length() % 4) % 4;
        return new String(Base64.getUrlDecoder().decode(value + "=".repeat(padding)), StandardCharsets.UTF_8);
    }

    private static String encode(String value) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(value.getBytes(StandardCharsets.UTF_8));
    }

    public static void main(String[] args) throws Exception {
        List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8);
        if (lines.size() < 3 || !INPUT_HEADER.equals(lines.get(0))) {
            throw new IllegalArgumentException("Unsupported P64-L08 3D input.");
        }
        String[] world = lines.get(1).split("\t");
        int width = Integer.parseInt(world[1]);
        int depth = Integer.parseInt(world[2]);
        int height = Integer.parseInt(world[3]);
        List<BoxItem> boxes = new ArrayList<>();
        for (int index = 2; index < lines.size(); index++) {
            String[] row = lines.get(index).split("\t");
            if (row.length != 5 || !"ITEM".equals(row[0])) {
                throw new IllegalArgumentException("Invalid P64-L08 item.");
            }
            Box box = Box.newBuilder()
                .withId(decode(row[1]))
                .withSize(Integer.parseInt(row[2]), Integer.parseInt(row[3]), Integer.parseInt(row[4]))
                .withRotate2D()
                .withWeight(1)
                .build();
            boxes.add(new BoxItem(box, 1));
        }
        Container container = Container.newBuilder()
            .withId("bgig-real-3d")
            .withSize(width, depth, height)
            .withMaxLoadWeight(boxes.size())
            .build();
        LargestAreaFitFirstPackager packager = LargestAreaFitFirstPackager.newBuilder().build();
        long started = System.nanoTime();
        PackagerResult result = packager.newResultBuilder()
            .withBoxItems(boxes)
            .withContainerItem(new ContainerItem(container, 1))
            .withMaxContainerCount(1)
            .build();
        double solveMs = (System.nanoTime() - started) / 1_000_000.0;
        List<String> output = new ArrayList<>();
        output.add(OUTPUT_HEADER);
        if (!result.isSuccess()) {
            output.add("RESULT\tunknown\t" + solveMs);
        } else {
            output.add("RESULT\tfeasible\t" + solveMs);
            for (Placement placement : result.get(0).getStack().getPlacements()) {
                BoxStackValue value = placement.getStackValue();
                output.add(
                    "PLACEMENT\t" + encode(placement.getBox().getId())
                    + "\t" + placement.getAbsoluteX()
                    + "\t" + placement.getAbsoluteY()
                    + "\t" + placement.getAbsoluteZ()
                    + "\t" + value.getDx()
                    + "\t" + value.getDy()
                    + "\t" + value.getDz()
                );
            }
        }
        Files.write(Path.of(args[1]), output, StandardCharsets.UTF_8);
        packager.close();
    }
}