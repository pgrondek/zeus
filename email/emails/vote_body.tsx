import {
    Button,
    Hr,
    Section,
    Text,
} from '@react-email/components';

import BaseTemplate from "../components/baseTemplate";
import Trans, {BlockTrans} from "../components/trans";

export const VoteBody = () => (
    <BaseTemplate title="Title">
        <Section style={box}>
            <Text style={paragraph}>
                <Trans text={`Dear voter,}`}/>
            </Text>
            {`{% if custom_message %}`}
            <Text style={paragraph}>
                {`{{custom_message|safe}}`}
            </Text>
            {`{% endif %}`}
            <Text style={paragraph}>
                <Trans text={`You are invited to vote in the poll:}`}/>
            </Text>
            <code className="inline-block py-4 px-[4.5%] w-9/10 bg-[#f4f4f4] rounded-md border border-solid border-[#eee] text-[#333]">
                {`{{election.name}}`}<br/>
                {`{ % block poll_name %}{{poll.name}}{% endblock %}`}<br/>
            </code>
            <Text style={paragraph}>
                {`{ % trans "starting} {{election.voting_starts_at}},`}
                {`{ % trans "and ending} {{election.voting_ends_at}}`}
                {`{ % trans "Your registration ID is:} {{voter.voter_login_id}}.`}
            </Text>
            <Text style={paragraph}>
                {`{ % trans "To submit your vote, follow the link below}`}
            </Text>
            <Button style={button} href="{{ voter.get_quick_login_url }}">
                {`{ % trans "Vote now}`}
            </Button>
            <Hr style={hr}/>
            <Text style={paragraph}>
                {`{ % trans "Information:}`}
            </Text>
            <ul>
                <li>{`{ % trans "You can vote more than once. Only your last vote will be counted.}`}</li>
                <li>
                    {`{ % trans "For information about the voting you can contact the trustees by phone,}`} <br/>
                    {`{{ election.help_phone }}`}<br/>
                    <Trans text={`or by email,}`}/><br/>
                    {`{{ election.help_email }}`}<br/>
                </li>
                {`{ % block audit_codes %}{% if voter.audit_passwords %}* If you want to initiate an audit vote,}`}
                <li>
                    <Trans text={`the valid audit codes are}`} /><br/>
                    <code
                        className="font-mono font-bold px-1 py-px bg-[#dfe1e4] text-[#3c4149] text-[21px] tracking-[-0.3px] rounded">
                        {`{ % for pass in voter.get_audit_passwords %}{{pass}}  {% endfor %}`}
                    </code> <br/>
                    <Trans text={`Otherwise ignore those codes above."%}`}/>
                </li>
                {`{% endblock %}`}
            </ul>
            <Hr style={hr} />
            <Text style={paragraph}>
                {`Important:`}
            </Text>
            <Text style={paragraph}>
                <BlockTrans text={`Important:

The present message is strictly personal and confidential.
Do not forward or show it to others. Do not reply to this.`}/>
                <Trans text={`Instead, you can write to`}/>{`{{election.help_email}}.`}
                <BlockTrans text={`If you are not the legitimate recipient, please delete this message
and contact helpdesk@zeus.grnet.gr`}/>
            </Text>
        </Section>
    </BaseTemplate>
);

export default VoteBody;


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
