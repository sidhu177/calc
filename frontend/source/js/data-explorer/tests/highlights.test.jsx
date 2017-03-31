import toJson from "enzyme-to-json";

import { Highlights } from "../components/highlights";
import makeSetup from "./testSetup";

const defaultProps = {
  stdDeviation: 1.1,
  avgPrice: 2.1,
  proposedPrice: 5
};

const setup = makeSetup(Highlights, defaultProps);

describe("<Highlights>", () => {
  it("renders correctly", () => {
    const { wrapper } = setup();

    expect(wrapper.find(".sd-highlight").first().text()).toBe("$1");
    expect(wrapper.find(".avg-price-highlight").text()).toBe("$2");
    expect(wrapper.find(".sd-highlight").last().text()).toBe("$3");
    expect(wrapper.find(".proposed-price-highlight").text()).toBe("$5");
  });

  it("matches snapshot", () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
