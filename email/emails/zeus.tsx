import {
    Button,
    Hr,
    Section,
    Text,
} from '@react-email/components';

import * as fs from "fs";
import BaseTemplate from "../components/baseTemplate";

export const ZeusEmail = () => (
    <BaseTemplate title="Zeus">
        <Section style={box}>
            <Text style={paragraph}>
                Szanowna osobo głosująca
            </Text>
            <Text style={paragraph}>
                Nadszedł czas decyzji!
            </Text>
            <Text style={paragraph}>
                Wybory do imperium galaktycznego
                Głosowanie 1
            </Text>
            <Text style={paragraph}>
                Aby zagłosować, kliknij na łącze poniżej
            </Text>
            <Button style={button} href="https://example.com/">
                Głosuj teraz
            </Button>
            <Hr style={hr} />
            <Text style={paragraph}>
                Informacja:
            </Text>
            <ul>
                <li>Możesz głosować więcej niż raz. Tylko ostatni głos zostanie policzony.</li>
                <li>
                    Aby uzyskać informacje o głosowaniu, możesz skontaktować się telefonicznie <br/>
                    None<br/>
                    lub przez e-mail<br/>
                    None<br/>
                </li>
                <li>
                    Aby wykonać głosowanie kontrolne, prawidłowe kody kontrolne to <br/>
                    <code className="font-mono font-bold px-1 py-px bg-[#dfe1e4] text-[#3c4149] text-[21px] tracking-[-0.3px] rounded">
                    2137  xyza  WTF1  abcd
                    </code> <br/>
                    W przeciwnym razie możesz zignorować podane powyżej kody.
                </li>
            </ul>
        </Section>
    </BaseTemplate>
);

export default ZeusEmail;

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

const button = {
    backgroundColor: '#0A212F',
    borderRadius: '5px',
    color: '#fff',
    fontSize: '16px',
    fontWeight: 'bold',
    textDecoration: 'none',
    textAlign: 'center' as const,
    display: 'block',
    width: '100%',
    padding: '10px',
};

const footer = {
    color: '#8898aa',
    fontSize: '12px',
    lineHeight: '16px',
};
