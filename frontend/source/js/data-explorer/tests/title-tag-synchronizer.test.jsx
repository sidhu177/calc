import { TitleTagSynchronizer } from "../components/title-tag-synchronizer";
import makeSetup from "./testSetup";

describe("<TitleTagSynchronzer>", () => {
  let fakeDocument;
  let mounted;

  const setup = extraProps => {
    fakeDocument = { title: "original" };

    mounted = makeSetup(TitleTagSynchronizer, {
      q: "",
      document: fakeDocument
    })(extraProps).mounted;
  };

  it("leaves title unchanged on mount if query is empty", () => {
    setup();
    expect(fakeDocument.title).toBe("original");
  });

  it("sets title to search query on mount if it is non-empty", () => {
    setup({ q: "blarg" });
    expect(fakeDocument.title).toBe("blarg - CALC Search");
  });

  it("sets title to non-empty search query on props change", () => {
    setup();
    mounted.setProps({ q: "boop," });
    expect(fakeDocument.title).toBe("boop - CALC Search");
  });

  it("sets title to original if query is empty on props change", () => {
    setup({ q: "boop" });
    mounted.setProps({ q: "" });
    expect(fakeDocument.title).toBe("original");
  });

  it("resets title to original on unmount", () => {
    setup({ q: "boop" });
    mounted.unmount();
    expect(fakeDocument.title).toBe("original");
  });
});
