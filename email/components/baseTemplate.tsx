import {
    Body,
    Button,
    Container,
    Head,
    Hr,
    Html,
    Img,
    Link,
    Preview,
    Section,
    Text,
} from '@react-email/components';

import * as fs from "fs";
import {Trans} from "./jinja2";

const baner = fs.readFileSync("./emails/static/zeus.png", "base64");

export const BaseTemplate = ({children, title} : {children: any, title: any} ) => (
    <>
        <Html>
            {`{% load i18n %}`}
            <Head />
            <Body style={main}>
                <Container style={container}>
                    <Img
                        src={`data:image/png;base64,${baner}`}
                        width="890"
                        height="150"
                        alt="Zeus"
                    />
                    {children}
                    <Section style={box}>
                        <Hr style={hr}/>
                        <Text style={footer}>
                            <Trans text={`Zeus Elections`}/>
                        </Text>
                    </Section>
                </Container>
            </Body>
        </Html>
    </>
);

export default BaseTemplate;

const main = {
    backgroundColor: '#f6f9fc',
    fontFamily:
        '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Ubuntu,sans-serif',
};

const container = {
    backgroundColor: '#ffffff',
    margin: '0 auto',
    padding: '20px 0 48px',
    marginBottom: '64px',
};

const box = {
    padding: '0 48px',
};

const hr = {
    borderColor: '#e6ebf1',
    margin: '20px 0',
};

const paragraph = {
    color: '#525f7f',

    fontSize: '16px',
    lineHeight: '24px',
    textAlign: 'left' as const,
};

const footer = {
    color: '#8898aa',
    fontSize: '12px',
    lineHeight: '16px',
};
