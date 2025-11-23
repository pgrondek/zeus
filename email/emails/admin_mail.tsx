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
import BaseTemplate from "../components/baseTemplate";
import Trans from "../components/trans";

export const AdminMail = () => (
    <BaseTemplate title={`{% trans \"System message\" %}: {{msg}}`}>
        <Section style={box}>
            <Text style={paragraph}>
                <Trans text={`System message`} />
                <code className="font-mono font-bold px-1 py-px bg-[#dfe1e4] text-[#3c4149] text-[21px] tracking-[-0.3px] rounded">
                    {`{{msg}}`}
                </code>
            </Text>
            <Text style={paragraph}>
                <Trans text={`ELECTION INFO`}/>
            </Text>
            <code className="inline-block py-4 px-[4.5%] w-9/10 bg-[#f4f4f4] rounded-md border border-solid border-[#eee] text-[#333]">
                {`Election name: {{election.name}}`}<br/>
                {`Election description: {{election.description}}`}<br/>
                {`Election type: {{election_type}}`}<br/>
                {`Starting date: {{election.voting_starts_at}}`}<br/>
                {`Ending date: {{election.voting_ends_at}}`}<br/>
                {`Ending date with extension": {{election.voting_extended_until}}`}<br/>
            </code>
            <Text style={paragraph}>
                <Trans text={`Trustees`}/>
            </Text>
            <ul>
                {`{% for trustee in trustees %}`}
                <li>{`{{trustee.name}} {{trustee.email}}`}</li>
                {`{% endfor %}`}
            </ul>
            <Text style={paragraph}>
                <Trans text={`ELECTION INFO`}/>
            </Text>
            <ul>
                {`{% for admin in admins %}`}
                <li>{`{{admin.id}}  {{admin.user_id}} {{admin.institution.name}}`}</li>
                {`{% endfor %}`}
            </ul>
        </Section>
    </BaseTemplate>
);

export default AdminMail;


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
